# Dockerfile

FROM nodesource/nsolid

COPY server.js /server.js

EXPOSE 8888

CMD ["nsolid", "/server.js"]

