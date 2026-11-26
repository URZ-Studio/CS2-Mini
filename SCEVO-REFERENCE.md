# SCEvo reference

Upstream: https://github.com/TeamKoprulu/SCEvoComplete/tree/773c8e8ae8828121e8f37bb74ab82ceb761a45bc

Native component layout of SC2_5015_Balance.SC2Mod: standard catalogs live in Base.SC2Data/GameData/ without a root manifest. SCEvo_Multi uses a root Includes file only for extra named catalogs, and registers trigger libraries in the nested GameData/GameData.xml CGame catalog. MiniCraft 0.1.11 adopts the native standard-catalog layout and preserves any existing manifest and CGame trigger registrations. No upstream balance values, Brood War units, graphics, or assets are imported. Engine validation still required.

MIT notice retained:

The MIT License (MIT)

Copyright (c) 2016 Abraham Yunes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
