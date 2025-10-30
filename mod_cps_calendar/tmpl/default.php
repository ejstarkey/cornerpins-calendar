<?php
defined('_JEXEC') or die;
?>

<div class="cps-calendar-wrapper" id="cps-calendar-<?php echo $module->id; ?>">
    
    <div class="cps-calendar-loading">
        <div class="bowling-ball-loader"></div>
        <p>Loading tournaments...</p>
    </div>
    
    <div class="cps-calendar-error" style="display: none;">
        <p>Unable to load calendar events. Please try again later.</p>
    </div>
    
    <div class="cps-calendar-content"></div>
    
</div>
