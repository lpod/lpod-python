# Copyright 1999-2009 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

NEED_PYTHON=2.6
inherit distutils

DESCRIPTION="languages & platforms OpenDocument - Python library"
HOMEPAGE="http://lpod-project.net"
SRC_URI="http://download.lpod-project.net/${PN}/${P}.tar.gz"

LICENSE="GPL-3 Apache-2.0"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE="doc"

DEPEND=""
RDEPEND=">=dev-python/lxml-2.0
         >=dev-python/pygobject-2.16.1
	 doc? ( =app-doc/lpod-docs-${PV} )"

