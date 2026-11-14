
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
    env:
    - name: DOCKER_CONFIG
      value: "/root/.docker"
    volumeMounts:
    - name: docker-config
      mountPath: /root/.docker/config.json
      subPath: .dockerconfigjson

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
      secretName: nexus-registry-secret

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
        IMAGE_NAME = "registry.praveeninfra.online/docker-private/portfolio-backend"
        IMAGE_TAG = "build-${BUILD_NUMBER}"

        GITOPS_REPO = "github.com:MytPraveen/portfolio-gitops.git"

        GIT_USER_NAME = "Jenkins CI"
        GIT_USER_EMAIL = "jenkins@ci.com"
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
                          --dockerfile $WORKSPACE/Dockerfile \
                          --destination=${IMAGE_NAME}:${IMAGE_TAG}
                    '''
                }
            }
        }

        stage('Security Scan') {
            steps {
                container('trivy') {
                    sh '''
                        trivy image \
                          --scanners vuln \
                          --severity HIGH,CRITICAL \
                          --ignore-unfixed \
                          --exit-code 1 \
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

                        sed -i "s|^[[:space:]]*image:.*|        image: ${IMAGE_NAME}:${IMAGE_TAG}|" \
                          production/backend/deployment.yaml

                        git diff -- production/backend/deployment.yaml

                        git add production/backend/deployment.yaml

                        git commit -m "Update backend image to ${IMAGE_TAG}"

                        git push origin main
                    '''
                }
            }
        }
    }

    post {
        success {
            echo """
            ========================================
            Backend Pipeline Successful
            Image: ${IMAGE_NAME}:${IMAGE_TAG}
            GitOps repository updated.
            ArgoCD will synchronize the deployment.
            ========================================
            """
        }

        failure {
            echo "Backend Pipeline Failed. Check the stage logs."
        }
    }
}
