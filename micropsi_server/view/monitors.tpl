<div>
    <script src="/static/js/d3.v2.min.js" type="text/javascript"></script>
    <script src="/static/js/monitor.js" type="text/javascript"></script>
    <div class="sectionbar">
        <form class="navbar-form">
            <div class="pull-right">
                <button data="vertical" class="layoutbtn btn active">◫</button>
                <button data="horizontal" class="layoutbtn btn" style="-webkit-transform: rotate(-90deg);
                        -moz-transform: rotate(-90deg);
                        -ms-transform: rotate(-90deg);
                        -o-transform: rotate(-90deg);">◫</button>
            </div>
            <table>
                <tr>
                    <td><span data-toggle="collapse" data-target="#monitor, #monitor_controls"><i
                            class="icon-chevron-right"></i></span></td>

                    <td data-toggle="collapse" data-target="#monitor, #monitor_controls"> Nodenet Monitor &nbsp;</td>
                    <td>
                        <div class="btn-group nodenet_list">
                            <a class="btn" href="#">
                                (no nodenet selected)
                            </a>
                        </div>
                    </td>

                    <td><div class="" id="monitor_controls collapse in">
                        <button class="add_custom_monitor btn">Add custom Monitor</button>
                        <button class="btn">Clear</button>
                    </div></td>

                </tr>
            </table>
        </form>
    </div>

    <div id="monitor" class="section-margin frontend_section collapse in">
        <div class="section multiple">
            <div class="monitor_field layout_field span6">
                <h4>Monitors</h4>
                <div class="contentbox section">
                    <div id="graph"></div>
                    <div class="monitor_seperator">
                        <form class="form-horizontal monitor_list">
                            <label for="monitor_x_axis">
                                No. of steps:
                            </label>
                            <select id="monitor_x_axis" class="input-mini">
                                <option>100</option>
                                <option>200</option>
                                <option>500</option>
                                <option>1000</option>
                                <option value="-1">all</option>
                            </select>
                        </form>
                        <ul id="monitor_selector" class="monitor_list">
                        </ul>
                    </div>
                </div>
            </div>
            <div class="logger_field layout_field span6">
                <h4>Logs</h4>
                <div class="contentbox section">
                    <div id="logs"></div>
                    <form class="form-horizontal span4 monitor_seperator">
                        <ul id="log_selector" class="monitor_list">
                            <li>
                                <label for="log_system" class="system_log">
                                    <input type="checkbox" id="log_system" class="log_switch" data="system" />
                                    System
                                </label>
                                <select id="level_log_system" class="log_level_switch" data="system">
                                    <option value="DEBUG" {{'selected="selected"' if logging_levels['system'] == "DEBUG" else ""}}>Debug</option>
                                    <option value="INFO" {{'selected="selected"' if logging_levels['system'] == "INFO" else ""}}>Info</option>
                                    <option value="WARNING" {{'selected="selected"' if logging_levels['system'] == "WARNING" else ""}}>Warning</option>
                                    <option value="ERROR" {{'selected="selected"' if logging_levels['system'] == "ERROR" else ""}}>Error</option>
                                </select>
                            </li>
                            <li>
                                <label for="log_world" class="world_log">
                                    <input type="checkbox" id="log_world" class="log_switch" data="world" />
                                    World
                                </label>
                                <select id="level_log_world" class="log_level_switch" data="world">
                                    <option value="DEBUG" {{'selected="selected"' if logging_levels['world'] == "DEBUG" else ""}}>Debug</option>
                                    <option value="INFO" {{'selected="selected"' if logging_levels['world'] == "INFO" else ""}}>Info</option>
                                    <option value="WARNING" {{'selected="selected"' if logging_levels['world'] == "WARNING" else ""}}>Warning</option>
                                    <option value="ERROR" {{'selected="selected"' if logging_levels['world'] == "ERROR" else ""}}>Error</option>
                                </select>
                            </li>
                            <li>
                                <label for="log_agent" class="agent_log">
                                    <input type="checkbox" id="log_agent" class="log_switch" data="agent" />
                                    Agent
                                </label>
                                <select id="level_log_agent" class="log_level_switch" data="agent">
                                    <option value="DEBUG" {{'selected="selected"' if logging_levels['agent'] == "DEBUG" else ""}}>Debug</option>
                                    <option value="INFO" {{'selected="selected"' if logging_levels['agent'] == "INFO" else ""}}>Info</option>
                                    <option value="WARNING" {{'selected="selected"' if logging_levels['agent'] == "WARNING" else ""}}>Warning</option>
                                    <option value="ERROR" {{'selected="selected"' if logging_levels['agent'] == "ERROR" else ""}}>Error</option>
                                </select>
                            </li>
                        </ul>
                    </form>
                    <form class="form-horizontal span4 monitor_list">
                        <p><label for="monitor_filter_logs">Filter:</label>
                        <input type="text" value="" id="monitor_filter_logs" class="input-small"/></p>

                        <!-- <p><label for="log_show_step" class="agent_log">
                            <input type="checkbox" id="log_show_step" class="log_show_step" data="" />
                            show nodenet step
                        </label></p> -->

                        <p><button id="clear_logs" class="btn btn-small">clear logs</button></p>
                    </form>
                </div>
            </div>
            <p style="clear:both">&nbsp;</p>
        </div>
    </div>
</div>