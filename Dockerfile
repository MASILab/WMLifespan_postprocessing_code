FROM kimm58/wm_lifespan_processing:v0.1

WORKDIR /SCRIPTS
RUN git clone https://github.com/MASILab/WMLifespan_postprocessing_code.git
RUN cp /SCRIPTS/WMLifespan_postprocessing_code/scripts/* /SCRIPTS
RUN chmod +x /SCRIPTS/*.sh
RUN chmod +x /SCRIPTS/*.py