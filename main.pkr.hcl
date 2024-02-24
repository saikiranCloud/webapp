variable "source_image" {
  default = "centos-stream-8-v20230509"
}

variable "project_id" {
  default = "tf-gcp-infra-002207381"
}

variable "network" {
  default = "default"
}

variable "disk_size" {
  default = 100
}

variable "zone" {
  default = "us-east1-b"
}

variable "disk_type" {
  default = "pd-standard"
}

variable "machine_type" {
  default = "e2-micro"
}

variable "ssh_username" {
  defaulting = "sai"
}

packer {
  required_plugins {
    googlecompute = {
      source  = "github.com/hashicorp/googlecompute"
      version = "~> 1"
    }
  }
}

source "googlecompute" "centos-python" {
  project_id           = var.project_id
  source_image         = var.source_image
  image_name           = "csye6225-${formatdate("YYYY-MM-DD-hh-mm-ss", timestamp())}"
  zone                 = var.zone
  disk_size            = var.disk_size
  wait_to_add_ssh_keys = "20s"
  network              = var.network
  communicator         = "ssh"
  ssh_username         = var.ssh_username
}

build {
  sources = ["source.googlecompute.centos-python"]
  provisioner "shell" {
    scripts = ["scripts/user_setup.sh"]
  }

  provisioner "file" {
    source      = "./webapp.zip"
    destination = "/tmp/webapp.zip"
  }

  provisioner "file" {
    source      = "webapp.service"
    destination = "/tmp/webapp.service"
  }

  provisioner "shell" {
    scripts = ["scripts/setup.sh"]
  }

  provisioner "shell" {
    scripts = ["scripts/app.sh"]
  }

  post-processor "manifest" {
    output = "image_manifest.json"
  }
}
