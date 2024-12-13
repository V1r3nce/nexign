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
        stage('Build and Run') {
            steps {
                script {

                    echo "python -V"
                    sh """
                    python --version
                    python main.py
                    """
                }
            }
        }
    }
}