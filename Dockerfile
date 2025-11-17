# Use a minimal, secure base image
FROM python:3.14-alpine

# Create a non-root user and group
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --home /app appuser

# Copy only necessary files
COPY src/ /app

# Set working directory
WORKDIR /app

# Install dependencies (if any)
RUN pip install --upgrade pip
RUN pip install requests

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the port your app runs on
EXPOSE 8080

# Use a non-root entrypoint
CMD ["python", "serve_gists.py"]