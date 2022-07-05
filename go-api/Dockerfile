FROM golang:1.18-alpine as builder
WORKDIR /build
COPY go.mod .
COPY go.sum .
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -o pixel-api .


# generate clean, final image for end users
FROM alpine:3
COPY --from=builder /build/pixel-api .
ENTRYPOINT [ "./pixel-api" ]