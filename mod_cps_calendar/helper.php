<?php
defined('_JEXEC') or die;

use Joomla\CMS\Factory;
use Joomla\CMS\Http\HttpFactory;

class ModCpsCalendarHelper
{
    protected $params;
    
    public function __construct($params)
    {
        $this->params = $params;
    }
    
    /**
     * Sanitize output
     */
    public static function sanitize($text)
    {
        return htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
    }
}
