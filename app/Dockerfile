
FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci --omit=dev

COPY app.js ./
COPY tracing.js ./

USER node

EXPOSE 3000

CMD ["node", "--require", "./tracing.js", "app.js"]

