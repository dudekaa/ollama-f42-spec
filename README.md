# Ollama

Quick and dirty [ollama](https://github.com/ollama/ollama) RPM package with systemd service.
It basically just builds the RPM package from official release tarball and adds a basic systemd service file.

The main motivation for this was the obsolete version in official Fedora repos. And missing unit file in the official
package.

## Installation
```bash
sudo dnf copr enable nost23/ollama && sudo dnf install ollama && systemctl start ollama
```

to start the service on every boot

```bash
sudo systemctl enable ollama
```

## Configuration
### 1\. Open the Drop-in File Editor

Create a **drop-in file** for the service.
```bash
sudo systemctl edit ollama.service
```
### 2\. Add the Environment Variable

Inside the editor, add an `[Service]` section and use the **`Environment` directive** to set your variable.

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_ORIGINS=*"
Environment="..."
```

### 3\. Reload and Restart the Service

Finally, you need to **reload the systemd daemon** to pick up the changes and then **restart the service** for the new
environment variables to take effect.

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama.service
```

Now, the service will have access to the custom environment variable you defined. You can verify this by checking
the service's status or by having the service log the variable's value.

## Inspired by
- https://github.com/mwprado/ollamad
- https://koji.fedoraproject.org/koji/buildinfo?buildID=2801184 - the official Fedora package
