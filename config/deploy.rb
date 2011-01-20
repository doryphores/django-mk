set :application, "Mario Kart"

set :domain, "192.168.1.134"

set :deploy_to, "/home/martin/www/django-mk-prod"
set :db_location, "src"
set :app_location, "src/mk"
set :apache_connector, "#{app_location}/apache/connector.wsgi"
set :static_location, "src/static"
set :django_admin_media, "/usr/local/lib/python2.6/dist-packages/django/contrib/admin/media"
set :backup_dir, "#{deploy_to}/backups"

set :keep_releases, 3

# User

set :user, "martin"
set :use_sudo, false

# Source control

set :repository,  "git@github.com:doryphores/django-mk.git"
set :branch, "develop"
set :scm, :git
set :deploy_via, :remote_cache
default_run_options[:pty] = true  # Must be set for the password prompt from git to work

role :web, domain
role :app, domain
role :db,  domain, :primary => true

namespace :backup do
  task :setup do
    run "mkdir -p #{deploy_to}/#{backup_dir}"
  end
  
  task :db do
    run "cp #{shared_path}/system/db.sqlite #{backup_dir}/db.#{Time.now.to_f}.sqlite"
  end
  
  after   "deploy:setup", "backup:setup"
  before  "deploy", "backup:db"
end

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
    run "rm -rf #{release_path}/#{static_location}/images/avatars"
    run "ln -nfs #{shared_path}/uploads/avatars #{release_path}/#{static_location}/images/avatars"
    run "rm -rf #{release_path}/#{static_location}/images/charts"
    run "ln -nfs #{shared_path}/uploads/charts #{release_path}/#{static_location}/images/charts"
  end
  
  desc <<-EOD
    [internal] Computes uploads directory paths
    and registers them in Capistrano environment.
  EOD
  task :register_dirs do
    set :uploads_dirs,    %w(uploads uploads/avatars uploads/charts)
    set :shared_children, fetch(:shared_children) + fetch(:uploads_dirs)
  end
  
  after       "deploy:finalize_update", "shared:symlink"
  after       "deploy:setup", "shared:setup"
  on :start,  "shared:register_dirs"
end

namespace :deploy do
  task :start do ; end
  task :stop do ; end
  task :finalize_update do
    run "chown -R :www-data #{latest_release}"
    run "chmod -R g+w #{latest_release}" if fetch(:group_writable, true)
    
    run "ln -s #{django_admin_media} #{latest_release}/#{static_location}/admin_media"
    run "ln -s #{shared_path}/system/local_settings.py #{latest_release}/#{app_location}/local_settings.py"
    run "ln -s #{shared_path}/system/db.sqlite #{latest_release}/#{db_location}/db.sqlite"
  end
  task :restart, :roles => :app, :except => { :no_release => true } do
    run "#{try_sudo} touch #{current_path}/#{apache_connector}"
  end
end

namespace :django do
  desc "Perform db migrations"
  task :migrate do
    run "#{current_path}/#{app_location}/manage.py syncdb --noinput --migrate"
  end
  
  desc "Re-run history"
  task :update do
    run "#{current_path}/#{app_location}/manage.py update_history --noinput"
  end
  
  after "deploy", "django:migrate", "django:update"
end