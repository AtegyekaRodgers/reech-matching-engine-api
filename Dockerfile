#==============================
# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

ARG PORT_ARG=8080
ARG PROJECT_ID_ARG=not-specified
ARG DATABASE_ARG=
ARG MONGO_DB_ARG=
ARG SMTP_SERVER_ARG=
ARG SMTP_PORT_ARG=587
ARG SMTP_USER_ARG=
ARG SMTP_PXWD_ARG=
ARG CLOUDINARY_CLOUD_NAME_ARG=
ARG CLOUDINARY_API_KEY_ARG=
ARG CLOUDINARY_API_SECRET_ARG=
#-----------------
ENV PORT=$PORT_ARG
ENV PROJECT_ID=$PROJECT_ID_ARG
ENV SECRET=$SECRET_ARG
ENV DATABASE=$DATABASE_ARG
ENV MONGO_DB=$MONGO_DB_ARG
ENV SMTP_SERVER=$SMTP_SERVER_ARG
ENV SMTP_PORT=$SMTP_PORT_ARG
ENV SMTP_USER=$SMTP_USER_ARG
ENV SMTP_PXWD=$SMTP_PXWD_ARG
ENV CLOUDINARY_CLOUD_NAME=$CLOUDINARY_CLOUD_NAME_ARG
ENV CLOUDINARY_API_KEY=$CLOUDINARY_API_KEY_ARG
ENV CLOUDINARY_API_SECRET=$CLOUDINARY_API_SECRET_ARG

ARG TAGGED_DOCKER_IMAGE=""

RUN pip install pip waitress --upgrade
WORKDIR /app

COPY requirements.txt .

# Create a virtual environment for the application
RUN python -m venv /opt/venv

# Upgrade pip and install dependencies within the virtual environment
RUN /opt/venv/bin/python -m pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

RUN ls && ls matching_engine

# Expose the port that the application will run on
EXPOSE 8080

ENTRYPOINT ["./matching_engine/launch.py"]

# Start the Waitress server and run the application
CMD /opt/venv/bin/waitress-serve --port=$PORT ${TAGGED_DOCKER_IMAGE}
