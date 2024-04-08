FROM artefact.skao.int/ska-tango-images-pytango-builder:9.5.0

ARG USER=newuser
ENV USER ${USER}
ENV HOME /home/${USER}
ENV PATH ${HOME}/.local/bin:${HOME}/.venv/bin:${PATH}

RUN userdel tango
RUN useradd --create-home --home-dir ${HOME} ${USER}
RUN usermod -u 1000 -g 1000 ${USER}

USER ${USER}

WORKDIR ${HOME}

COPY --chown=${USER}:${USER} . ./

RUN poetry install
