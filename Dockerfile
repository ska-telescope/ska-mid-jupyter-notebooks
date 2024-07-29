FROM registry.gitlab.com/ska-telescope/ska-mid-itf-engineering-tools/ska-mid-itf-engineering-tools:0.9.2-dev.c2a87082a

ARG USER=newuser
ENV USER ${USER}
ENV HOME /home/${USER}
ENV PATH ${HOME}/.local/bin:${HOME}/.venv/bin:${PATH}

#RUN userdel tango
RUN useradd --create-home --home-dir ${HOME} ${USER}
RUN usermod -u 1000 -g 1000 ${USER}

USER ${USER}

WORKDIR ${HOME}

COPY --chown=${USER}:${USER} . ./

RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    sed -i '/pytango/d' poetry-requirements.txt && \
    sed -i '/numpy/d' poetry-requirements.txt && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:${HOME}/src:${HOME}/.venv/lib/python3.10/site-packages"
ENV PATH="${HOME}/bin:${HOME}/.venv/bin:/root/.local/bin:${PATH}"
