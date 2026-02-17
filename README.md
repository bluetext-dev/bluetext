# Bluetext

A development framework built on Polytope for accelerating enterprise-grade application development with intelligent coding assistance.

## Prerequisites

### Install Polytope

```bash
curl https://polytope.com/install.sh | sh
```

### Make `pt` Available

If the `pt` command is not on your PATH after installation:

**Current session only:**
```bash
export PATH="~/.local/bin/polytope:$PATH" && source ~/.zshrc
```

**Permanently:**
```bash
echo 'export PATH="~/.local/bin/polytope:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

## Setup

### Step 1: Start the Polytope MCP Server

From the `bluetext` directory:

```bash
pt run --mcp
```

### Step 2: Configure Your MCP Client

#### Claude Code

Add the MCP server to Claude Code:

```bash
claude mcp add polytope --transport sse http://localhost:81883/mcp
```

#### Cline

Due to a known issue in Cline, you must run a port-forwarding command in a separate terminal:

```bash
sudo socat TCP-LISTEN:80,fork TCP:localhost:81883
```

Keep this terminal session running while using Bluetext with Cline.

Then add the following to your Cline MCP config:

```json
{
  "mcpServers": {
    "polytope": {
      "type": "streamableHttp",
      "url": "http://localhost/mcp",
      "disabled": false
    }
  }
}
```

## Usage

Once setup is complete, you can use Bluetext through any MCP-compatible client.

To verify your setup, try a sample prompt:

> Use polytope to build a website with a contact form and save its contents
