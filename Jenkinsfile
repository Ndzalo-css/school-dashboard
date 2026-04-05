pipeline {
    agent any

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
        KUBECONFIG = "C:\\Users\\ndzal\\.kube\\config"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${GIT_BRANCH}",
                    credentialsId: "${GITHUB_CREDENTIALS}",
                    url: "${GIT_REPO}"
            }
        }

        stage('Show Files') {
            steps {
                bat '''
                echo Listing project files
                dir
                '''
            }
        }

        stage('Check Tools') {
            steps {
                bat '''
                echo Checking installed tools...
                git --version
                docker --version
                kubectl version --client
                '''
            }
        }

        stage('OWASP Dependency Check') {
            steps {
                bat '''
                where dependency-check.bat >nul 2>nul
                if %errorlevel%==0 (
                    dependency-check.bat --project "school-dashboard" --scan . --format "HTML" --out dependency-check-report
                ) else (
                    echo OWASP Dependency Check not installed on Jenkins agent, skipping for now.
                )
                '''
            }
        }

        stage('SonarQube Scan') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    bat '''
                    where sonar-scanner.bat >nul 2>nul
                    if %errorlevel%==0 (
                        sonar-scanner.bat ^
                          -Dsonar.projectKey=school-dashboard ^
                          -Dsonar.projectName=school-dashboard ^
                          -Dsonar.sources=. ^
                          -Dsonar.sourceEncoding=UTF-8
                    ) else (
                        echo sonar-scanner not installed on Jenkins agent, skipping for now.
                    )
                    '''
                }
            }
        }

        stage('Build Frontend Image') {
            steps {
                bat '''
                docker build -t %FRONTEND_IMAGE%:%IMAGE_TAG% -f Dockerfile .
                docker tag %FRONTEND_IMAGE%:%IMAGE_TAG% %FRONTEND_IMAGE%:latest
                '''
            }
        }

        stage('Build Backend Image') {
            steps {
                bat '''
                docker build -t %BACKEND_IMAGE%:%IMAGE_TAG% -f Dockerfile.backend .
                docker tag %BACKEND_IMAGE%:%IMAGE_TAG% %BACKEND_IMAGE%:latest
                '''
            }
        }

        stage('Trivy Scan Frontend') {
            steps {
                bat '''
                where trivy >nul 2>nul
                if %errorlevel%==0 (
                    trivy image --exit-code 0 --severity HIGH,CRITICAL %FRONTEND_IMAGE%:%IMAGE_TAG%
                ) else (
                    echo Trivy not installed on Jenkins agent, skipping for now.
                )
                '''
            }
        }

        stage('Trivy Scan Backend') {
            steps {
                bat '''
                where trivy >nul 2>nul
                if %errorlevel%==0 (
                    trivy image --exit-code 0 --severity HIGH,CRITICAL %BACKEND_IMAGE%:%IMAGE_TAG%
                ) else (
                    echo Trivy not installed on Jenkins agent, skipping for now.
                )
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
                    bat '''
                    docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                    docker push %FRONTEND_IMAGE%:%IMAGE_TAG%
                    docker push %FRONTEND_IMAGE%:latest
                    docker push %BACKEND_IMAGE%:%IMAGE_TAG%
                    docker push %BACKEND_IMAGE%:latest
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                bat '''
                kubectl apply -f k8s/namespace.yaml
                kubectl apply -f k8s/

                kubectl set image deployment/school-frontend school-frontend=%FRONTEND_IMAGE%:%IMAGE_TAG% -n school-dashboard
                kubectl set image deployment/school-backend school-backend=%BACKEND_IMAGE%:%IMAGE_TAG% -n school-dashboard

                kubectl rollout status deployment/school-frontend -n school-dashboard
                kubectl rollout status deployment/school-backend -n school-dashboard
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'dependency-check-report/**/*', allowEmptyArchive: true
            bat 'kubectl get pods -n school-dashboard'
            bat 'kubectl get svc -n school-dashboard'
        }
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}