// ---------------------------------------------------------------
// Jenkinsfile — CI/CD-пайплайн проекта Iris Classifier
// Стадии: Checkout -> Install -> Lint -> Unit tests -> Docker build -> Smoke test
//         -> Push to Docker Hub
// ---------------------------------------------------------------
pipeline {
    // Выполнять на любом доступном исполнителе (у нас это сам Jenkins)
    agent any

    // Каждую минуту проверять GitHub: если появился новый коммит — запустить сборку
    triggers {
        pollSCM('* * * * *')
    }

    options {
        skipDefaultCheckout(true)                       // скачиваем код в отдельной стадии
        timestamps()                                    // время у каждой строки лога
        disableConcurrentBuilds()                       // не запускать две сборки одновременно
        buildDiscarder(logRotator(numToKeepStr: '30'))  // хранить 30 последних сборок
        timeout(time: 20, unit: 'MINUTES')              // аварийное ограничение по времени
    }

    environment {
        IMAGE_NAME = 'iris-api'
        PIP_CACHE_DIR = '/var/jenkins_home/.cache/pip'  // кэш pip между сборками
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                // Скачать код того коммита, который запустил сборку
                checkout scm
                script {
                    // Тег образа = номер сборки + короткий хеш коммита, например 5-a1b2c3d
                    def shortSha = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    env.IMAGE_TAG = "${env.BUILD_NUMBER}-${shortSha}"
                    currentBuild.description = "${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                }
                echo "Код получен. Тег образа: ${env.IMAGE_TAG}"
            }
        }

        stage('Install dependencies') {
            steps {
                // Чистое виртуальное окружение для каждой сборки
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                // Проверка стиля кода: любое замечание flake8 остановит сборку
                sh '.venv/bin/flake8'
            }
        }

        stage('Unit tests') {
            steps {
                sh '''
                    .venv/bin/pytest -v \
                        --junitxml=test-results.xml \
                        --cov=src --cov-report=term --cov-report=xml:coverage.xml
                '''
            }
            post {
                always {
                    // Отчёт о тестах (страница Test Result и график)
                    junit testResults: 'test-results.xml', allowEmptyResults: true
                    // Отчёт о покрытии кода тестами
                    recordCoverage(tools: [[parser: 'COBERTURA', pattern: 'coverage.xml']])
                }
            }
        }

        stage('Docker build') {
            steps {
                sh '''
                    docker build --progress=plain \
                        --build-arg APP_VERSION=$IMAGE_TAG \
                        -t $IMAGE_NAME:$IMAGE_TAG \
                        -t $IMAGE_NAME:latest \
                        .
                    docker images $IMAGE_NAME
                '''
            }
        }

        stage('Smoke test') {
            environment {
                SMOKE_CONTAINER = "iris-smoke-${BUILD_NUMBER}"
            }
            steps {
                // Запускаем собранный образ и проверяем, что сервис реально отвечает
                sh '''
                    docker run -d --name $SMOKE_CONTAINER $IMAGE_NAME:$IMAGE_TAG

                    echo "Ждём, пока контейнер станет healthy..."
                    for i in $(seq 1 30); do
                        STATUS=$(docker inspect -f '{{.State.Health.Status}}' $SMOKE_CONTAINER)
                        echo "  попытка $i: $STATUS"
                        [ "$STATUS" = "healthy" ] && break
                        sleep 2
                    done

                    if [ "$STATUS" != "healthy" ]; then
                        echo "Контейнер не стал healthy. Логи контейнера:"
                        docker logs $SMOKE_CONTAINER
                        exit 1
                    fi

                    docker exec -i $SMOKE_CONTAINER python - < scripts/smoke_test.py
                '''
            }
            post {
                always {
                    // Тестовый контейнер удаляем в любом случае
                    sh 'docker rm -f $SMOKE_CONTAINER || true'
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                // Логин и токен берутся из хранилища Jenkins Credentials (ID: dockerhub-credentials).
                // В коде их нет, а в логе Jenkins токен заменяется звёздочками.
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials',
                                                  usernameVariable: 'DOCKERHUB_USER',
                                                  passwordVariable: 'DOCKERHUB_TOKEN')]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin

                        docker tag $IMAGE_NAME:$IMAGE_TAG $DOCKERHUB_USER/$IMAGE_NAME:$IMAGE_TAG
                        docker tag $IMAGE_NAME:$IMAGE_TAG $DOCKERHUB_USER/$IMAGE_NAME:latest

                        docker push $DOCKERHUB_USER/$IMAGE_NAME:$IMAGE_TAG
                        docker push $DOCKERHUB_USER/$IMAGE_NAME:latest
                    '''
                    script {
                        // Полное имя образа в Docker Hub, понадобится на этапе деплоя
                        env.DOCKERHUB_IMAGE = "${env.DOCKERHUB_USER}/${env.IMAGE_NAME}"
                        currentBuild.description = "${env.DOCKERHUB_IMAGE}:${env.IMAGE_TAG}"
                    }
                }
            }
            post {
                always {
                    // Выходим из Docker Hub, чтобы не оставлять токен на сервере
                    sh 'docker logout || true'
                }
            }
        }
    }

    post {
        success {
            echo "Сборка успешна: образ ${env.DOCKERHUB_IMAGE}:${env.IMAGE_TAG} опубликован в Docker Hub"
        }
        failure {
            echo 'Сборка упала: откройте стадию, отмеченную красным, и посмотрите лог'
        }
        cleanup {
            // Очистить рабочую папку после сборки
            cleanWs()
        }
    }
}