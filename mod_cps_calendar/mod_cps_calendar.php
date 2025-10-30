<?php
defined('_JEXEC') or die;

use Joomla\CMS\Helper\ModuleHelper;
use Joomla\CMS\Factory;
use Joomla\Registry\Registry;

require_once __DIR__ . '/helper.php';

// FIX: Convert params to Registry object if it's a string
if (is_string($module->params)) {
    $params = new Registry($module->params);
} else {
    $params = $module->params;
}

$helper = new ModCpsCalendarHelper($params);

// Load CSS and JS
$wa = Factory::getApplication()->getDocument()->getWebAssetManager();
$wa->registerAndUseStyle('mod_cps_calendar', 'media/mod_cps_calendar/css/calendar.css');
$wa->registerAndUseScript('mod_cps_calendar', 'media/mod_cps_calendar/js/calendar.js', [], ['defer' => true]);

// Pass config to JavaScript
$config = [
    'apiEndpoint' => $params->get('api_endpoint', 'https://cornerpins.com.au/api'),
    'cacheDuration' => $params->get('cache_duration', 300),
    'eventsLimit' => $params->get('events_limit', 50),
    'moduleId' => $module->id
];

Factory::getApplication()->getDocument()->addScriptOptions('mod_cps_calendar_' . $module->id, $config);

require ModuleHelper::getLayoutPath('mod_cps_calendar', $params->get('layout', 'default'));