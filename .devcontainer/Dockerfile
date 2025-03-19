# Use Fedora as base image
FROM fedora:latest

# Update the system and install necessary packages
RUN dnf update -y && \
    dnf install -y python3.12 python3-pip make git && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Create a non-root user and set up the development environment
RUN useradd -m pokerApp && \
    echo "pokerApp:$(openssl passwd -6 ${USER_PWD})" | chpasswd -e && \
    usermod -aG wheel pokerApp && \
    mkdir -p /home/pokerApp/development && \
    chown -R pokerApp:pokerApp /home/pokerApp

# Switch to the non-root user
USER pokerApp

# Set the working directory
WORKDIR /home/pokerApp/development/

# Set the PATH to include the location where pip installs executables
ENV PATH=/home/pokerApp/.local/bin:$PATH
ENV MYPYPATH=/home/pokerApp/development/PokerApp/pokerApp
# Clone the repository as the non-root user and install requirements 
RUN git clone -b dev https://github.com/niclaurio/PokerApp.git && \
    cd PokerApp && \
    make install && \
    pre-commit install

# Expose app port
EXPOSE 8000

CMD ["tail", "-f", "/dev/null"]