pipeline {
    agent any

    environment {
        APP_NAME = "school-dashboard"
        DOCKERHUB_CREDENTIALS = "dockerhub-creds"
        GITHUB_CREDENTIALS = "github-creds"
        DOCKERHUB_USERNAME = "ndzalo9707"
        FRONTEND_IMAGE = "${DOCKERHUB_USERNAME}/school-dashboard-frontend"
        BACKEND_IMAGE = "${DOCKERHUB_USERNAME}/school-dashboard-backend"
        IMAGE_TAG = "${BUILD_NUMBER}"
        GIT_REPO = "https://github.com/Ndzalo-css/school-dashboard.git"
        GIT_BRANCH = "main"
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

        // ✅ NEW STAGE (SonarQube)
   stage('SonarQube Scan') {
    steps {
        withSonarQubeEnv('sonarqube-server') {
            script {
                def scannerHome = tool 'sonar-scanner'
                bat """
                ${scannerHome}\\bin\\sonar-scanner ^
                  -Dsonar.projectKey=school-dashboard ^
                  -Dsonar.projectName=school-dashboard ^
                  -Dsonar.sources=. ^
                  -Dsonar.sourceEncoding=UTF-8
                """
            }
        }
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
                where trivy
                exit /b 0
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
                exit /b 0
                '''
            }
        }

        stage('Build Frontend Image') {
            steps {
                dir('frontend') {
                    bat '''
                    echo Building frontend Docker image...
                    docker build -t %FRONTEND_IMAGE%:%IMAGE_TAG% .
                    docker tag %FRONTEND_IMAGE%:%IMAGE_TAG% %FRONTEND_IMAGE%:latest
                    '''
                }
            }
        }

        stage('Build Backend Image') {
            steps {
                dir('backend') {
                    bat '''
                    echo Building backend Docker image...
                    docker build -t %BACKEND_IMAGE%:%IMAGE_TAG% -f Dockerfile.backend .
                    docker tag %BACKEND_IMAGE%:%IMAGE_TAG% %BACKEND_IMAGE%:latest
                    '''
                }
            }
        }

        stage('Trivy Scan Frontend') {
            steps {
                bat '''
                where trivy >nul 2>nul
                if %errorlevel%==0 (
                    trivy image --exit-code 0 --severity HIGH,CRITICAL %FRONTEND_IMAGE%:%IMAGE_TAG%
                ) else (
                    echo Trivy not installed on Jenkins agent, skipping frontend image scan.
                )
                exit /b 0
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
                    echo Trivy not installed on Jenkins agent, skipping backend image scan.
                )
                exit /b 0
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
                    echo Logging into Docker Hub...
                    docker login -u %DOCKER_USER% -p %DOCKER_PASS%

                    echo Pushing frontend image...
                    docker push %FRONTEND_IMAGE%:%IMAGE_TAG%
                    docker push %FRONTEND_IMAGE%:latest

                    echo Pushing backend image...
                    docker push %BACKEND_IMAGE%:%IMAGE_TAG%
                    docker push %BACKEND_IMAGE%:latest
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                bat '''
                echo Applying Kubernetes manifests...
                kubectl apply -f k8s/namespace.yaml
                kubectl apply -f k8s/

                echo Updating deployment images...
                kubectl set image deployment/school-frontend school-frontend=%FRONTEND_IMAGE%:%IMAGE_TAG% -n school-dashboard
                kubectl set image deployment/school-backend school-backend=%BACKEND_IMAGE%:%IMAGE_TAG% -n school-dashboard

                echo Waiting for rollout...
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