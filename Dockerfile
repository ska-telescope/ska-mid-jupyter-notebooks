FROM artefact.skao.int/ska-mid-itf-engineering-tools:0.9.2

ENV HOME /app

WORKDIR ${HOME}


RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    sed -i '/pytango/d' poetry-requirements.txt && \
    sed -i '/numpy/d' poetry-requirements.txt && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt

COPY . ${HOME}
    
RUN poetry install
    
USER root
    
ENV PATH=${HOME}:/app/.venv/bin/:$PATH