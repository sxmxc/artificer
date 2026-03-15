FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

USER root

EXPOSE 3000

CMD ["sh", "./start.sh"]
