FROM python:3.12-alpine AS build-env
RUN apk add --no-cache build-base findutils libffi-dev python3-dev
RUN pip install --upgrade pip
RUN pip install tox flake8
COPY ./ /usr/src/somebot
WORKDIR /usr/src/somebot
RUN tox && pip wheel -w /build .

FROM python:3.12-alpine
WORKDIR /
RUN apk add --no-cache dumb-init tzdata
COPY --from=build-env /build /build
COPY startup /usr/local/bin/startup
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN pip install --upgrade pip \
    && pip install -f /build /build/*.whl \
    && chmod +x /usr/local/bin/startup \
    && rm -rf /build
ENTRYPOINT ["/usr/bin/dumb-init", "--",  "startup"]
