// Test attivazione automatica Jenkins tramite GitHub Webhook
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

        stage('Health Check') {
            steps {
                powershell '''
                    $maxRetries = 10
                    $success = $false

                    for ($i = 1; $i -le $maxRetries; $i++) {
                        try {
                            $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5

                            if ($response.status -eq "healthy") {
                                Write-Host "Health Check OK"
                                $success = $true
                                break
                            }
                        }
                        catch {
                            Write-Host "Tentativo $i fallito. Attendo 3 secondi..."
                            Start-Sleep -Seconds 3
                        }
                    }

                    if (-not $success) {
                        throw "Health Check fallito: servizio non disponibile"
                    }
                '''
            }
        }


    }

    post {
    success {
        echo """
        ========================================
        PIPELINE COMPLETATA CON SUCCESSO
        Job: ${env.JOB_NAME}
        Build: ${env.BUILD_NUMBER}
        Immagine: ${env.IMAGE_NAME}:${env.BUILD_NUMBER}
        Risultato: SUCCESS
        ========================================
        """
    }

    failure {
        echo """
        ========================================
        PIPELINE FALLITA
        Job: ${env.JOB_NAME}
        Build: ${env.BUILD_NUMBER}
        Risultato: FAILURE
        Controllare la Console Output di Jenkins.
        ========================================
        """
    }
}
}
