
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'sentiment-analysis'
        CONTAINER_NAME = 'sentiment-analysis'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% .'
            }
        }

        stage('Test') {
            steps {
                bat 'docker run --rm %IMAGE_NAME%:%BUILD_NUMBER% python -m pytest -v tests/'
            }
        }

        stage('Deploy') {
            steps {
                bat '''
                    docker rm -f %CONTAINER_NAME% 2>NUL
                    docker run -d --name %CONTAINER_NAME% -p 8000:8000 %IMAGE_NAME%:%BUILD_NUMBER%
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completata con successo!'
        }

        failure {
            echo 'Pipeline fallita: controllare i log Jenkins.'
        }
    }
}
