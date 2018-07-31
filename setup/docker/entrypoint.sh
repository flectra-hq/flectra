#!/bin/bash

set -e

# set the postgres database host, port, user and password according to the environment
# and pass them as arguments to the flectra process if not present in the config file
: ${HOST:=${DB_PORT_5432_TCP_ADDR:='db'}}
: ${PORT:=${DB_PORT_5432_TCP_PORT:=5432}}
: ${USER:=${DB_ENV_POSTGRES_USER:=${POSTGRES_USER:='flectra'}}}
: ${PASSWORD:=${DB_ENV_POSTGRES_PASSWORD:=${POSTGRES_PASSWORD:='flectra'}}}

DB_ARGS=()
function check_config() {
    param="$1"
    value="$2"
    DB_ARGS+=("--${param}")
    DB_ARGS+=("${value}")
}
if [[ -z "${IGNORE_ENV}" ]]; then
    check_config "db_host" "$HOST"
    check_config "db_port" "$PORT"
    check_config "db_user" "$USER"
    check_config "db_password" "$PASSWORD"
fi

case "$1" in
    -- | flectra)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            exec /opt/flectra/flectra-bin "$@"
        else
            exec /opt/flectra/flectra-bin "$@" "${DB_ARGS[@]}"
        fi
        ;;
    -*)
        exec /opt/flectra/flectra-bin "$@" "${DB_ARGS[@]}"
        ;;
    *)
        exec "$@"
esac

exit 1
