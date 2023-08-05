// for friend classes: their cpp files can use this header to access
// implementation

#ifndef FORMAST_MODULE_IMPL_HPP_INCLUDED
#define FORMAST_MODULE_IMPL_HPP_INCLUDED

#include <boost/shared_ptr.hpp>
#include <boost/variant/recursive_variant.hpp>

#include "formast.hpp"

namespace formast
{
namespace detail
{

typedef boost::make_recursive_variant<formast::Class, formast::Enum>::type ModuleDecl;

}
}

class formast::Module::Impl : public std::vector<formast::detail::ModuleDecl>
{
private:
    // see http://www.boost.org/doc/libs/1_51_0/libs/smart_ptr/sp_techniques.html#pimpl
    Impl(Impl const &);
    Impl & operator=(Impl const &);
public:
    Impl();
};

#endif
