set :application, "Mario Kart"

set :domain, "doryphores.net"

set :deploy_to, "/opt/django-projects/mk"
set :apache_connector, "apache/production.wsgi"
set :backup_dir, "#{deploy_to}/backups"
set :virtualenv_root, "#{shared_path}/system/env"
set :requirements_file, "#{release_path}/requirements/prod.txt"

set :python, "#{virtualenv_root}/bin/python"

set :keep_releases, 3

set :shared_children, %w(media system log data)

# User

set :user, "ubuntu"
set :use_sudo, false

# Source control

set :repository,  "git@github.com:doryphores/django-mk.git"
set :scm, :git
set :deploy_via, :remote_cache
#default_run_options[:pty] = true  # Must be set for the password prompt from git to work

set :branch do
  default_tag = `git tag`.split("\n").last

  tag = Capistrano::CLI.ui.ask "Tag to deploy (make sure to push the tag first, A to abort): [#{default_tag}] "
  tag = default_tag if tag.empty?
  if tag == 'A' then
    error = CommandError.new("Aborted")
    raise error
  end
  tag
end

role :web, domain
role :app, domain
role :db,  domain, :primary => true


# Python virtual environment

namespace :env do
  desc <<-EOD
    Creates virtual environment for application
  EOD
  task :setup do
    run "virtualenv --distribute --no-site-packages #{virtualenv_root}"
  end
  
  desc <<-EOD
    Symlinks virtual environment
  EOD
  task :symlink do
    run "ln -nfs #{virtualenv_root} #{release_path}/env"
  end
  
  desc <<-EOD
    Updates virtual environment libraries from requirements file
  EOD
  task :update_requirements do
    run "pip install -q -E #{virtualenv_root} --requirement #{requirements_file}"
  end
  
  after "deploy:setup", "env:setup"
end


# Backups

namespace :backup do
  desc <<-EOD
    Creates backup folder
  EOD
  task :setup do
    run "mkdir -p #{backup_dir}"
  end
  
  desc <<-EOD
    Creates backup of db (simple copy of sqlite file with timestamp)
  EOD
  task :db do
    run "cp #{shared_path}/data/db.sqlite #{backup_dir}/db.#{Time.now.to_f}.sqlite"
  end
  
  after "deploy:setup", "backup:setup"
end


# Shared folders and assets

namespace :shared do
  desc <<-EOD
    Sets group and permissions on shared folders
  EOD
  task :setup, :except => { :no_release => true } do
    run "chown -R :www-data #{shared_path}"
    run "chmod g+w #{shared_path}"
  end
  
  desc <<-EOD
    Creates symlinks to shared folders and other assets
    for the most recently deployed version.
  EOD
  task :symlink, :except => { :no_release => true } do
  	# Media assets folder
    run "rm -rf #{release_path}/public/media"
    run "ln -nfs #{shared_path}/media #{release_path}/public/media"

    # Database
    run "rm -rf #{release_path}/data"
    run "ln -s #{shared_path}/data #{latest_release}/data"
    
    # Local settings (if any exist)
    run "if [ -f #{shared_path}/system/local_settings.py ]; then ln -s #{shared_path}/system/local_settings.py #{latest_release}/local_settings.py; fi"
  end
  
  after "deploy:setup", "shared:setup"
end


# Django tasks

def django_manage(cmd, options={})
  run "cd #{latest_release}; #{python} manage.py #{cmd}", options
end

namespace :django do
  desc "Perform db migrations"
  task :migrate do
    django_manage "syncdb --noinput --migrate"
  end
  
  desc "Collect static files"
  task :collectstatic do
    django_manage "collectstatic --noinput -l"
  end
  
  desc "Re-run history"
  task :update_history do
    django_manage "update_history --noinput"
  end
  
  desc "Cleanup"
  task :cleanup do
    django_manage "cleanup"
  end
end


# Override default capistrano tasks

namespace :deploy do
  task :start do ; end
  task :stop do ; end
  task :finalize_update do
    backup.db
    shared.symlink
    env.update_requirements
    env.symlink
    django.migrate
    django.collectstatic
    django.update_history
    django.cleanup
  end
  task :restart, :roles => :app, :except => { :no_release => true } do
    # Touch WSGI script to restart app
    run "#{try_sudo} touch #{current_path}/#{apache_connector}"
  end
end

after "deploy", "deploy:cleanup"
