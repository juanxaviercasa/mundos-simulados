<?php

if (!defined('ABSPATH')) {
    exit;
}

class MundoSimuladosResearchManager {
    public function collect($query, $providers) {
        $results = [];
        foreach ($providers as $provider) {
            if (get_transient('ms_research_blocked_' . $provider)) {
                continue;
            }

            $provider_results = $this->fetch($provider, $query);
            if (is_wp_error($provider_results)) {
                if (in_array($provider_results->get_error_code(), ['quota', 'auth'], true)) {
                    set_transient('ms_research_blocked_' . $provider, 1, HOUR_IN_SECONDS);
                }
                update_option('ms_research_last_error_' . $provider, sanitize_text_field($provider_results->get_error_message()), false);
                continue;
            }

            if ($provider_results) {
                $results[$provider] = $provider_results;
            }
        }

        update_option('ms_research_last_run', current_time('mysql'), false);
        return $results;
    }

    private function fetch($provider, $query) {
        $url = '';
        $args = ['timeout' => 20, 'headers' => []];
        if ($provider === 'search_console' && get_option('ms_search_console_token') && get_option('ms_search_console_site')) {
            $url = 'https://www.googleapis.com/webmasters/v3/sites/' . rawurlencode(get_option('ms_search_console_site')) . '/searchAnalytics/query';
            $args['headers']['Authorization'] = 'Bearer ' . get_option('ms_search_console_token');
            $args['headers']['Content-Type'] = 'application/json';
            $args['method'] = 'POST';
            $args['body'] = wp_json_encode(['startDate' => gmdate('Y-m-d', strtotime('-28 days')), 'endDate' => gmdate('Y-m-d', strtotime('-2 days')), 'dimensions' => ['query'], 'rowLimit' => 25]);
        } elseif ($provider === 'bing_webmaster' && get_option('ms_bing_webmaster_key') && get_option('ms_bing_webmaster_site')) {
            $url = add_query_arg(['siteUrl' => get_option('ms_bing_webmaster_site'), 'apikey' => get_option('ms_bing_webmaster_key')], 'https://ssl.bing.com/webmaster/api.svc/json/GetRankAndTrafficStats');
        } elseif ($provider === 'brave' && ($key = get_option('ms_brave_search_key'))) {
            $url = add_query_arg(['q' => $query, 'count' => 10], 'https://api.search.brave.com/res/v1/web/search');
            $args['headers']['X-Subscription-Token'] = $key;
        } elseif ($provider === 'bing' && ($key = get_option('ms_bing_search_key'))) {
            $url = add_query_arg(['q' => $query, 'count' => 10], 'https://api.bing.microsoft.com/v7.0/search');
            $args['headers']['Ocp-Apim-Subscription-Key'] = $key;
        } elseif ($provider === 'google' && get_option('ms_google_search_key') && get_option('ms_google_search_cx')) {
            $url = add_query_arg(['key' => get_option('ms_google_search_key'), 'cx' => get_option('ms_google_search_cx'), 'q' => $query, 'num' => 10], 'https://www.googleapis.com/customsearch/v1');
        } elseif ($provider === 'youtube' && ($key = get_option('ms_youtube_key'))) {
            $url = add_query_arg(['part' => 'snippet', 'q' => $query, 'maxResults' => 10, 'type' => 'video', 'key' => $key], 'https://www.googleapis.com/youtube/v3/search');
        } elseif ($provider === 'reddit') {
            $url = add_query_arg(['q' => $query, 'sort' => 'relevance', 'limit' => 10, 'raw_json' => 1], 'https://www.reddit.com/search.json');
            $args['headers']['User-Agent'] = get_option('ms_reddit_user_agent', 'MundoSimuladosSuite/1.0');
        }

        if (!$url) {
            return [];
        }

        $response = $provider === 'search_console' ? wp_safe_remote_post($url, $args) : wp_safe_remote_get($url, $args);
        if (is_wp_error($response)) {
            return new WP_Error('network', $response->get_error_message());
        }

        $code = wp_remote_retrieve_response_code($response);
        if ($code === 401 || $code === 403) {
            return new WP_Error('auth', 'Credencial rechazada por ' . $provider . '.');
        }
        if ($code === 429 || $code === 402) {
            return new WP_Error('quota', 'Cuota agotada en ' . $provider . '.');
        }
        if ($code < 200 || $code >= 300) {
            return new WP_Error('provider', 'Error HTTP ' . $code . ' en ' . $provider . '.');
        }

        return $this->normalize($provider, json_decode(wp_remote_retrieve_body($response), true));
    }

    private function normalize($provider, $data) {
        $items = [];
        if ($provider === 'search_console') {
            $items = $data['rows'] ?? [];
        } elseif ($provider === 'bing_webmaster') {
            $items = $data['d']['results'] ?? $data['d'] ?? [];
        } elseif ($provider === 'brave') {
            $items = $data['web']['results'] ?? [];
        } elseif ($provider === 'bing' || $provider === 'google') {
            $items = $data['webPages']['value'] ?? $data['items'] ?? [];
        } elseif ($provider === 'youtube') {
            $items = $data['items'] ?? [];
        } elseif ($provider === 'reddit') {
            $items = array_map(static function ($item) { return $item['data'] ?? []; }, $data['data']['children'] ?? []);
        }

        $normalized = [];
        foreach (array_slice($items, 0, 10) as $item) {
            $permalink = !empty($item['permalink']) ? 'https://www.reddit.com' . $item['permalink'] : '';
            $normalized[] = [
                'title' => sanitize_text_field($item['title'] ?? $item['keys'][0] ?? $item['query'] ?? $item['snippet']['title'] ?? ''),
                'description' => sanitize_textarea_field($item['description'] ?? $item['snippet']['description'] ?? $item['selftext'] ?? (isset($item['clicks']) ? 'Clicks: ' . $item['clicks'] . ', impresiones: ' . ($item['impressions'] ?? 0) : '')),
                'url' => esc_url_raw($item['url'] ?? $item['link'] ?? $permalink)
            ];
        }

        return array_filter($normalized, static function ($item) { return $item['title'] || $item['description']; });
    }
}
