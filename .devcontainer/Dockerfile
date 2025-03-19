# Use Fedora as the base image
FROM fedora:latest

# Update system packages and install required dependencies (Python, Git, Make)
RUN dnf update -y && \
    dnf install -y python3.12 python3-pip make git && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Create a non-root user (pokerApp), set password, and create the development directory
RUN useradd -m pokerApp && \
    echo "pokerApp:$(openssl passwd -6 ${USER_PWD})" | chpasswd -e && \
    usermod -aG wheel pokerApp && \
    mkdir -p /home/pokerApp/development && \
    chown -R pokerApp:pokerApp /home/pokerApp

# Switch to the non-root user
USER pokerApp

# Set the working directory to the development folder
WORKDIR /home/pokerApp/development/

# Update PATH to include the location where pip installs executables
ENV PATH=/home/pokerApp/.local/bin:$PATH

# Set custom environment variable for the Python project
ENV MYPYPATH=/home/pokerApp/development/PokerApp/pokerApp

# Clone the repository and install dependencies using Make
RUN git clone -b dev https://github.com/niclaurio/PokerApp.git && \
    cd PokerApp && \
    make install && \
    pre-commit install

# Expose port 8000 for the application
EXPOSE 8000

# Default command to keep the container running
CMD ["tail", "-f", "/dev/null"]
