properties([parameters([
    choice(name: 'headless', choices: ['False', 'True'], description: 'Режим браузера (с GUI или без)')
])])

// CRON_SETTINGS = BRANCH_NAME == "master" ? '''0 0 * * * % headless==False''' : ""


def agent_label = '(woi-rhel8 && docker) || woi-tmp-rhel8-docker'

// == Константы для стиля разделителей в параметрах сборки ==

def separator_section_header_style = """
	background-color: #bff04e;
	text-align: center;
	padding: 4px;
	color: #343434;
    font-size: 22px;
	font-weight: normal;
	text-transform: uppercase;
	font-family: Open Sans, sans-serif;
	letter-spacing: 1px;
	font-style: italic;
"""
def separator_style = "border-width: 0"

pipeline {
    agent {
        label agent_label
    }
    options {
        timestamps ()
        timeout(time: 1, unit: 'HOURS')
        ansiColor('xterm')
        // Разрешение на копирование артефактов из этого job другими Jenkins job
        copyArtifactPermission('*')
    }
//     triggers {
//         parameterizedCron(CRON_SETTINGS)
//     }
    stages {
        stage('Prepare workspace') {
            steps {
                echo '--- Clean up workspace ---'
                cleanWs()
                echo '--- Checkout scm ---'
                checkout(scm)
            }
        }
        stage("Run tests") {
            steps {
                echo '--- Run tests ---'
                script {
                    docker.image('docker.nexign.com/playwright/python:latest').inside {
                        sh """
                            pip install -r requirements.txt
                            playwright install chromium
                            python3 -m pytest tests/t.py --headless --alluredir=${WORKSPACE}/allure-results
                        """
                    }
                }
            }
        }
        stage('Allure Report') {
            steps {
                allure commandline: 'allure-2.18.1', includeProperties: false, jdk: '', results: [[path: '${WORKSPACE}/allure-results']]            }
        }
    }
    post {
        success {
            cleanWs deleteDirs:true
        }
    }
}
