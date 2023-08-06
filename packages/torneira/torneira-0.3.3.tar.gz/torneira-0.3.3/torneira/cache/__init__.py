# -*- coding: utf-8 -*-

# Licensed under the Open Software License ("OSL") v. 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.opensource.org/licenses/osl-3.0.php

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from torneira.cache.extension import CachedQuery, CachedExtension
from torneira.cache.util import get_cache, cache_key, cached, cached_timeout, async_cached

__all__ = (
    'CachedQuery',
    'CachedExtension',
    'get_cache',
    'cache_key',
    'cached',
    'cached_timeout',
    'async_cached'
)
