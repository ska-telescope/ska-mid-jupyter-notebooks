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

RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    sed -i '/pytango/d' poetry-requirements.txt && \
    sed -i '/numpy/d' poetry-requirements.txt && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt 

RUN mkdir data

RUN curl https://gitlab.com/ska-telescope/sdp/ska-sdp-realtime-receive-core/-/raw/main/data/AA05LOW.ms.tar.gz --output data/AA05LOW.ms.tar.gz

RUN cd data/ && tar -xzf AA05LOW.ms.tar.gz && cd ..
