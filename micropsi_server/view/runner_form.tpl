
<div class="dialogform modal">

    <form class="form-horizontal" action="{{action}}" method="POST">

    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal">×</button>
      <h3>Runner Properties</h3>
    </div>

    <div class="modal-body">

            %if defined('error') and error:
            <div class="alert alert-info">
                <b>Error:</b> {{error}}.
            </div>
            %end

            <fieldset class="well">

                %if not defined("name_error"):
                <div class="control-group">
                %else:
                <div class="control-group error">
                %end
                    <label class="control-label" for="timestep">Interval in milliseconds</label>
                    <div class="controls">
                        <input type="text" class="input-xlarge" maxlength="256" id="timestep" name="timestep" value="{{value['timestep']}}" />
                        %if defined("name_error"):
                        <span class="help-inline">{{name_error}}</span>
                        %end
                    </div>
                </div>
                %if not defined("name_error"):
                <div class="control-group">
                %else:
                <div class="control-group error">
                %end
                    <label class="control-label" for="factor">Nodenet-steps per world step:</label>
                    <div class="controls">
                        <input type="text" class="input-xlarge" maxlength="256" id="factor" name="factor" value="{{value['factor']}}" />
                        %if defined("name_error"):
                        <span class="help-inline">{{name_error}}</span>
                        %end
                    </div>
                </div>
            </fieldset>
    </div>

    <div class="modal-footer">
        <button type="submit" class="btn btn-primary">Save</button>
        <a class="btn" data-dismiss="modal">Cancel</a>
    </div>

    </form>

</div>
