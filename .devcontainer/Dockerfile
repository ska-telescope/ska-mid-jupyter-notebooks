FROM registry.gitlab.com/ska-telescope/ska-mid-itf-engineering-tools/ska-mid-itf-engineering-tools:0.9.1

ARG USERNAME=tango
ARG USER_UID=1001
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME
