# ---------------------------------------------------------------
# Образ Jenkins с инструментами, нужными нашему CI/CD-пайплайну
# ---------------------------------------------------------------

# Официальный образ Jenkins (LTS-версия, Java 21, Debian 13)
FROM jenkins/jenkins:2.580.2-jdk21

# Для установки программ нужны права администратора
USER root

# 1. Python 3 + venv (для unit-тестов) и Docker CLI (для сборки образов).
#    Docker CLI ставим из официального репозитория Docker, как в документации Jenkins.
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv curl ca-certificates \
 && install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \
 && chmod a+r /etc/apt/keyrings/docker.asc \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
      > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends docker-ce-cli docker-buildx-plugin \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 2. kubectl — утилита управления Kubernetes (понадобится на этапе 8)
RUN curl -fsSL -o /usr/local/bin/kubectl \
      "https://dl.k8s.io/release/$(curl -fsSL https://dl.k8s.io/release/stable.txt)/bin/linux/$(dpkg --print-architecture)/kubectl" \
 && chmod +x /usr/local/bin/kubectl

# Возвращаемся к обычному пользователю jenkins
USER jenkins

# 3. Плагины Jenkins, которые нужны нашему пайплайну
COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt