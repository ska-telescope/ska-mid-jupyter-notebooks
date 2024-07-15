FROM artefact.skao.int/ska-tango-images-pytango-builder:9.5.0

ENV HOME /app

WORKDIR ${HOME}


#RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
#    sed -i '/pytango/d' poetry-requirements.txt && \
#    sed -i '/numpy/d' poetry-requirements.txt && \
#    pip install -r poetry-requirements.txt && \
#    rm poetry-requirements.txt
    
#RUN poetry install
    
USER root
    
ENV PATH=${HOME}:/app/.venv/bin/:$PATH