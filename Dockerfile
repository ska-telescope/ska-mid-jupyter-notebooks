FROM artefact.skao.int/ska-mid-itf-engineering-tools:0.9.2

#ARG USER=newuser
#ENV USER ${USER}
ENV HOME /app

#ENV PATH ${HOME}/.local/bin:${HOME}/.venv/bin:${PATH}

#RUN userdel tango
#RUN useradd --create-home --home-dir ${HOME} ${USER}
#RUN usermod -u 1000 -g 1000 ${USER}

#USER ${USER}

WORKDIR ${HOME}

#COPY --chown=${USER}:${USER} . ./

RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    sed -i '/pytango/d' poetry-requirements.txt && \
    sed -i '/numpy/d' poetry-requirements.txt && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt

COPY . ${HOME}
    
RUN poetry install
    
USER root
    
ENV PATH=${HOME}:/app/.venv/bin/:$PATH