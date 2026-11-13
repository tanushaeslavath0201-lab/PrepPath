
pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/YOUR_USERNAME/PrepPath.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Build') {
            steps {
                bat 'python -m compileall app.py'
            }
        }

        stage('Test') {
            steps {
                bat 'python -c "import app; print(\'PrepPath import successful\')"'
            }
        }

        stage('Deploy') {
            steps {
                echo 'PrepPath build and checks completed.'
                echo 'Ready for Docker deployment.'
            }
        }
    }
}
