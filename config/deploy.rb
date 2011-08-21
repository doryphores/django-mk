set :application, "Mario Kart"

set :domain, "doryphores.net"

set :deploy_to, "/opt/django-projects/mk"
set :db_location, "db.sqlite"
set :apache_connector, "apache/production.wsgi"
set :static_location, "static"
set :backup_dir, "#{deploy_to}/backups"
set :virtualenv_root, "#{shared_path}/system/env"
set :requirements_file, "#{release_path}/requirements/prod.txt"

set :keep_releases, 3

# User

set :user, "ubuntu"
set :use_sudo, false

# Source control

set :repository,  "git@github.com:doryphores/django-mk.git"
set :scm, :git
set :deploy_via, :remote_cache
default_run_options[:pty] = true  # Must be set for the password prompt from git to work

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


# Environment

namespace :env do
  task :setup do
    run "virtualenv --no-site-packages #{virtualenv_root}"
  end
  
  task :symlink do
    run "ln -nfs #{virtualenv_root} #{release_path}/env"
  end
  
  task :update_requirements do
    run "pip install -q -E #{virtualenv_root} --requirement #{requirements_file}"
  end
  
  after "deploy:setup", "env:setup"
  after "deploy:finalize_update", "env:symlink", "env:update_requirements"
end


# Backups

namespace :backup do
  task :setup do
    run "mkdir -p #{backup_dir}"
  end
  
  task :db do
    run "cp #{shared_path}/system/db.sqlite #{backup_dir}/db.#{Time.now.to_f}.sqlite"
  end
  
  after   "deploy:setup", "backup:setup"
  after   "deploy", "backup:db"
end


# Shared folders

namespace :shared do
  desc <<-EOD
    Creates the shared folders unless they exist
    and sets the group
  EOD
  task :setup, :except => { :no_release => true } do
    run "chown -R :www-data #{shared_path}"
  end
  
  desc <<-EOD
    [internal] Creates symlinks to shared folders
    for the most recently deployed version.
  EOD
  task :symlink, :except => { :no_release => true } do
    run "rm -rf #{release_path}/media"
    run "ln -nfs #{shared_path}/media #{release_path}/media"
  end
  
  desc <<-EOD
    [internal] Computes uploads directory paths
    and registers them in Capistrano environment.
  EOD
  task :register_dirs do
    set :uploads_dirs,    %w(media)
    set :shared_children, fetch(:shared_children) + fetch(:uploads_dirs)
  end
  
  after       "deploy:finalize_update", "shared:symlink"
  after       "deploy:setup", "shared:setup"
  on :start,  "shared:register_dirs"
end


# Override default capistrano tasks

namespace :deploy do
  task :start do
  end
  task :stop do ; end
  task :finalize_update do
    run "chown -R :www-data #{latest_release}"
    run "chmod -R g+w #{latest_release}" if fetch(:group_writable, true)
    
    # Symlink database
    run "ln -s #{shared_path}/system/db.sqlite #{latest_release}/#{db_location}"
  end
  task :restart, :roles => :app, :except => { :no_release => true } do
    # Touch WSGI script to restart app
    run "#{try_sudo} touch #{current_path}/#{apache_connector}"
  end
end


# Django specific tasks

def django_manage(cmd, options={})
  run "cd #{latest_release}; python manage.py #{cmd}", options
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
  task :update do
    django_manage "update_history --noinput"
  end
  
  desc "Cleanup"
  task :cleanup do
    django_manage "cleanup"
  end
  
  after "deploy", "django:migrate", "django:cleanup", "django:update", "deploy:cleanup", "deploy:collectstatic"
end
