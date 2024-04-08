FROM artefact.skao.int/ska-tango-images-pytango-builder:9.5.0

ARG USER=newuser
ENV USER ${USER}
ENV HOME /home/${USER}
ENV PATH /home/${USER}/.local/bin:${PATH}

RUN userdel tango
RUN useradd --create-home --home-dir /home/${USER} ${USER}
RUN usermod -u 1000 -g 1000 ${USER}

WORKDIR ${HOME}

COPY --chown=${USER}:${USER} . ./

USER ${USER}

COPY pyproject.toml poetry.lock ./

RUN poetry install
