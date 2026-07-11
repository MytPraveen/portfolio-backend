pipeline {

    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:

  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command: ["/busybox/sh"]
    args: ["-c", "sleep 999999"]
    tty: true
    volumeMounts:
    - name: docker-config
      mountPath: /kaniko/.docker/config.json
      subPath: .dockerconfigjson
    - name: workspace
      mountPath: /workspace

  - name: trivy
    image: aquasec/trivy:latest
    command: ["sh"]
    args: ["-c", "sleep 999999"]
    tty: true

  - name: git
    image: alpine/git:latest
    command: ["sh"]
    args: ["-c", "apk add --no-cache openssh && sleep 999999"]
    tty: true
    env:
    - name: GIT_SSH_COMMAND
      value: "ssh -o StrictHostKeyChecking=no -i /root/.ssh/id_ed25519"

    volumeMounts:
    - name: github-ssh
      mountPath: /root/.ssh
      readOnly: true

  volumes:

  - name: docker-config
    secret:
      secretName: dockerhub-secret

  - name: workspace
    emptyDir: {}

  - name: github-ssh
    secret:
      secretName: github-ssh-key
      defaultMode: 0400
"""
        }
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {

        IMAGE_NAME="praveendevops95/portfolio-backend"
        IMAGE_TAG="v${BUILD_NUMBER}"

        GITOPS_REPO="github.com:MytPraveen/portfolio-gitops.git"

        GIT_USER_NAME="Jenkins CI"
        GIT_USER_EMAIL="jenkins@ci.com"

    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {

                container('kaniko') {

                    sh '''

                    /kaniko/executor \
                      --context $WORKSPACE \
                      --dockerfile Dockerfile \
                      --destination=${IMAGE_NAME}:${IMAGE_TAG} \
                      --destination=${IMAGE_NAME}:latest

                    '''

                }
            }
        }

        stage('Security Scan') {

            steps {

                container('trivy') {

                    sh '''

                    trivy image \
                    --severity HIGH,CRITICAL \
                    --exit-code 0 \
                    ${IMAGE_NAME}:${IMAGE_TAG}

                    '''

                }

            }

        }

        stage('Update GitOps Repo') {

            steps {

                container('git') {

                    sh '''

                    git clone git@${GITOPS_REPO}

                    cd portfolio-gitops

                    git config user.name "${GIT_USER_NAME}"
                    git config user.email "${GIT_USER_EMAIL}"

                    sed -i "s|image:.*|image: ${IMAGE_NAME}:${IMAGE_TAG}|g" \
                    production/backend/deployment.yaml

                    git add .

                    git commit -m "Update backend image to ${IMAGE_TAG}" || true

                    git push origin main

                    '''

                }

            }

        }

    }

    post {

        success {

            echo "========================================"

            echo "Backend Deployment Successful"

            echo "Image : ${IMAGE_NAME}:${IMAGE_TAG}"

            echo "ArgoCD will deploy automatically."

            echo "========================================"

        }

        failure {

            echo "Pipeline Failed"

        }

    }

}
