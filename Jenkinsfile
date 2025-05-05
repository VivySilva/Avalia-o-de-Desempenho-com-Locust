pipeline {
    agent any

    environment {
        DOCKER_IMAGE_NAME = 'thainhat104/spring-petclinic'
        COMMIT_ID = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        BRANCH_NAME = "${env.BRANCH_NAME}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Test') {
            steps {
                sh './mvnw clean package -DskipTests'
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    def services = [
                        [name: 'admin-server', port: 9090],
                        [name: 'api-gateway', port: 8080],
                        [name: 'customers-service', port: 8081],
                        [name: 'discovery-server', port: 8761],
                        [name: 'vets-service', port: 8083],
                        [name: 'visits-service', port: 8082],
                        [name: 'genai-service', port: 8084]
                    ]

                    def changedServices = []

                    for (service in services) {
                        def serviceDir = "spring-petclinic-${service.name}"
                        def isChanged = sh(
                            script: "git diff --name-only HEAD~1 HEAD | grep -q '^${serviceDir}/'",
                            returnStatus: true
                        ) == 0

                        if (isChanged) {
                            changedServices << service
                        }
                    }

                    if (changedServices.isEmpty()) {
                        echo '✅ Không có service nào thay đổi. Bỏ qua bước Docker build.'
                    } else {
                        for (service in changedServices) {
                            def serviceName = service.name
                            def servicePort = service.port

                            def jarFile = findFiles(glob: "spring-petclinic-${serviceName}/target/*.jar")[0].path
                            sh "cp ${jarFile} docker/${serviceName}.jar"

                            sh """
                                docker build -t ${DOCKER_IMAGE_NAME}-${serviceName}:${COMMIT_ID} \
                                    --build-arg ARTIFACT_NAME=${serviceName} \
                                    --build-arg EXPOSED_PORT=${servicePort} \
                                    -f ./docker/Dockerfile ./docker

                                docker tag ${DOCKER_IMAGE_NAME}-${serviceName}:${COMMIT_ID} ${DOCKER_IMAGE_NAME}-${serviceName}:latest
                            """

                            sh "rm docker/${serviceName}.jar"
                        }

                        // Lưu danh sách service đã build để dùng ở bước push
                        writeFile file: 'changed-services.txt', text: changedServices*.name.join('\n')
                    }
                }
            }
        }

        stage('Docker Push') {
            when {
                expression { fileExists('changed-services.txt') }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    script {
                        echo "🔐 Logging in to Docker Hub as user: ${DOCKER_USER}"
                        sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'

                        def changedServices = readFile('changed-services.txt').split('\n')
                        for (service in changedServices) {
                            sh """
                                docker push ${DOCKER_IMAGE_NAME}-${service}:${COMMIT_ID}
                                docker push ${DOCKER_IMAGE_NAME}-${service}:latest
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
            sh 'docker system prune -f || true'
        }
    }
}
