pipeline {
    agent any

    tools {
        jdk 'jdk17'
        nodejs 'node18'
    }

    environment {
        APP_NAME = "school-dashboard"
        DOCKERHUB_CREDENTIALS = "dockerhub-creds"
        GITHUB_CREDENTIALS = "github-creds"
        DOCKERHUB_USERNAME = "Ndzalo9707"
        FRONTEND_IMAGE = "${DOCKERHUB_USERNAME}/school-dashboard-frontend"
        BACKEND_IMAGE = "${DOCKERHUB_USERNAME}/school-dashboard-backend"
        IMAGE_TAG = "${BUILD_NUMBER}"
        GIT_REPO = "https://github.com/Ndzalo-css/school-dashboard.git"
        GIT_BRANCH = "main"
        SONARQUBE_ENV = "sonarqube-server"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${GIT_BRANCH}", url: "${GIT_REPO}"
            }
        }

        stage('Show Files') {
            steps {
                sh '''
                echo "Listing project files"
                ls -la
                '''
            }
        }

        stage('OWASP Dependency Check') {
            steps {
                sh '''
                if command -v dependency-check.sh >/dev/null 2>&1; then
                  dependency-check.sh \
                    --project "school-dashboard" \
                    --scan . \
                    --format "HTML" \
                    --out dependency-check-report || true
                else
                  echo "OWASP Dependency Check not installed on Jenkins agent, skipping for now."
                fi
                '''
            }
        }

        stage('SonarQube Scan') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    sh '''
                    if command -v sonar-scanner >/dev/null 2>&1; then
                      sonar-scanner \
                        -Dsonar.projectKey=school-dashboard \
                        -Dsonar.projectName=school-dashboard \
                        -Dsonar.sources=. \
                        -Dsonar.sourceEncoding=UTF-8
                    else
                      echo "sonar-scanner not installed on Jenkins agent, skipping for now."
                    fi
                    '''
                }
            }
        }

        stage('Build Frontend Image') {
            steps {
                sh '''
                docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} -f Dockerfile .
                docker tag ${FRONTEND_IMAGE}:${IMAGE_TAG} ${FRONTEND_IMAGE}:latest
                '''
            }
        }

        stage('Build Backend Image') {
            steps {
                sh '''
                docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} -f Dockerfile.backend .
                docker tag ${BACKEND_IMAGE}:${IMAGE_TAG} ${BACKEND_IMAGE}:latest
                '''
            }
        }

        stage('Trivy Scan Frontend') {
            steps {
                sh '''
                if command -v trivy >/dev/null 2>&1; then
                  trivy image --exit-code 0 --severity HIGH,CRITICAL ${FRONTEND_IMAGE}:${IMAGE_TAG}
                else
                  echo "Trivy not installed on Jenkins agent, skipping for now."
                fi
                '''
            }
        }

        stage('Trivy Scan Backend') {
            steps {
                sh '''
                if command -v trivy >/dev/null 2>&1; then
                  trivy image --exit-code 0 --severity HIGH,CRITICAL ${BACKEND_IMAGE}:${IMAGE_TAG}
                else
                  echo "Trivy not installed on Jenkins agent, skipping for now."
                fi
                '''
            }
        }

        stage('Push Images') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKERHUB_CREDENTIALS}",
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                    docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
                    docker push ${FRONTEND_IMAGE}:latest
                    docker push ${BACKEND_IMAGE}:${IMAGE_TAG}
                    docker push ${BACKEND_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Update Kubernetes Manifests') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${GITHUB_CREDENTIALS}",
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_PASS'
                )]) {
                    sh '''
                    sed -i "s|image: .*school-dashboard-frontend:.*|image: ${FRONTEND_IMAGE}:${IMAGE_TAG}|g" k8s/frontend-deployment.yaml
                    sed -i "s|image: .*school-dashboard-backend:.*|image: ${BACKEND_IMAGE}:${IMAGE_TAG}|g" k8s/backend-deployment.yaml

                    git config user.name "jenkins"
                    git config user.email "jenkins@local"

                    git add k8s/frontend-deployment.yaml k8s/backend-deployment.yaml
                    git commit -m "Update Kubernetes image tags to ${IMAGE_TAG}" || true

                    git remote set-url origin https://${GIT_USER}:${GIT_PASS}@github.com/Ndzalo-css/school-dashboard.git
                    git push origin ${GIT_BRANCH}
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'dependency-check-report/**/*', allowEmptyArchive: true
        }
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}