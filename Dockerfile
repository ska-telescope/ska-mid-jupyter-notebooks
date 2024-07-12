FROM artefact.skao.int/ska-mid-itf-engineering-tools:0.9.2

ARG USER=newuser
ENV USER ${USER}
ENV HOME /home/${USER}
ENV PATH ${HOME}/.local/bin:${HOME}/.venv/bin:${PATH}
RUN useradd --create-home --home-dir ${HOME} ${USER}
RUN usermod -u 1000 -g 1000 ${USER}
WORKDIR ${HOME}
COPY --chown=${USER}:${USER} . ./
#RUN rm /usr/local/bin/poetry
USER ${USER}
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    sed -i '/pytango/d' poetry-requirements.txt && \
    sed -i '/numpy/d' poetry-requirements.txt && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt && curl -sSL https://install.python-poetry.org | python3 - --uninstall
ENV PYTHONPATH="${PYTHONPATH}:${HOME}/src:${HOME}/.venv/lib/python3.10/site-packages"
ENV PATH="${HOME}/bin:${HOME}/.venv/bin:/root/.local/bin:${PATH}"

