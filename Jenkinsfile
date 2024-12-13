properties([parameters([
    choice(name: 'headless', choices: ['False', 'True'], description: 'Режим браузера (с GUI или без)')
])])

CRON_SETTINGS = BRANCH_NAME == "master" ? '''0 0 * * * % headless==False''' : ""

pipeline {
    agent any
    triggers {
        parameterizedCron(CRON_SETTINGS)
    }
    stages {
        stage('Prepare Workspace'){
            steps{
                script{
                    sh"""
                        python -m venv venv
                        . .venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        python --version
                    """
                }
            }
        }
        stage('Build and Run') {
            steps {
                script {
                    sh """
                    . .venv/bin/activate
                    python -m pytest tests/t.py
                    """
                }
            }
        }
    }
}