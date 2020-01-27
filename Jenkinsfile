pipeline {
    agent any
    stages {
        stage("Checkout") {
            steps {
                checkout scm
                sh "echo 'COMPOSE_PROJECT_NAME=${env.JOB_NAME}-${env.BUILD_ID}' > .env"
                sh "docker --version; docker-compose --version"
            }
        }
        stage("Build") {
            steps {
                sh "docker-compose build --build-arg uid=`id -u` --build-arg gid=`id -g` lib"
                sh "docker-compose run --rm lib virtualenv .venv"
                sh "docker-compose run --rm lib .venv/bin/pip install -r requirements.txt"
            }
        }
        stage("Test") {
            steps {
                sh "docker-compose run --rm lib .venv/bin/pytest"
            }
        }
        stage("Flake 8") {
            steps {
                sh "if docker-compose run --rm lib .venv/bin/flake8 colormaps > flake8.txt; then echo 'flake8 is a success'; else cat flake8.txt; false; fi"
            }
        }
    }
    post {
        always {
            sh "docker-compose down --volumes --remove-orphans && docker-compose rm -f"
        }
    }
}
