FROM nginx:alpine
COPY nginx.conf.tmpl /etc/nginx/templates/nginx.conf.tmpl
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]