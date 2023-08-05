/* vi: set expandtab ts=4 sw=4:
 *
 * C++-implementation for stripping markup language from
 * normal strings and unicode strings.
 */
// Debugging support - remove comment to enable tracing
//# define DO_TRACE

# include <Python.h>
# include <algorithm>

# ifdef DO_TRACE
#   include <string>
#   include <iostream>
#   define TRACE(s) do { \
        std::cerr << s;  \
} while (false)
# else
#   define TRACE(s)
# endif

using std::min;

namespace {
    /**
     * Verify if 'in' is a tag or an end tag (non empty string ending with a
     * blank or '>').
     *
     * @param inp
     * Begin of input string (the first character after '<')
     *
     * @param end
     * End of input string
     *
     * @return
     * Pointer to element name ignoring '/'. If we do not have
     * a tag/end tag, 0 will be returned.
     */
    template <class Char>
    inline
    const Char *_is_element (const Char *in, const Char *end) {
        if (in == end)
            return (0);

        if (*in == '/')
            ++in;

        return (((in != end) &&
                 (*in != ' ') &&
                 (*in != '>'))? in: 0);
    }

    /*
     * Debugging support
     * Specializable for single char types to generate debug output.
     */
    template <class Char>
    inline
    const Char *is_element (const Char *in, const Char *end) {
        return (_is_element (in, end));
    }

    /**
     * Count elements of an array.
     *
     * @param v
     * Array which elements shall be counted
     *
     * @return
     * Number of contained elements
     */
    template<class V>
    size_t dim(const V &v) {
        return (sizeof (v) / sizeof (v[0]));
    }

    /**
     * Verify if the given tag is a 'script' tag.
     *
     * @param s
     * Begin of input string (the first character after '<')
     *
     * @param end
     * End of input string
     *
     * @return
     * true, if we have a 'script' tag
     */
    template <class Char>
    inline
    bool _is_script_tag (const Char *s, const Char *end) {
        static const Char script_tag[] = { 's', 'c', 'r', 'i', 'p', 't' };

        return (
            (size_t (end - s) == dim (script_tag)) &&
            (memcmp (
                s,
                script_tag,
                sizeof (script_tag)) == 0));
    }

    /*
     * Debugging thunk
     * Specializable for single char types to generate debug output.
     */
    template <class Char>
    bool is_script_tag (const Char *s, const Char *end) {
        return (_is_script_tag (s, end));
    }

    /*******************************************************************
     * Debug support
     * Define DO_TRACE to trace the results of is_element and is_script_tag.
     */
# ifdef DO_TRACE
    template <>
    inline
    const char *is_element<char> (const char *in, const char *end) {
        const char *result = _is_element (in, end);

        std::cerr << "is_element ("
                  << std::string (in, end - in)
                  << ") --> "
                  << (result
                         ? std::string (result, end - result)
                         : std::string ("(null)"))
                  << "\n"
            ;

        return (result);
    }

    template<>
    bool is_script_tag<char> (const char *s, const char *e) {
        bool result (_is_script_tag<char> (s, e));

        std::cerr << "is_script_tag ("
                  << std::string (s, e - s)
                  << ") --> "
                  << result
                  << "\n"
            ;

        return (result);
    }

    template <class T>
    struct auto_array {
        explicit auto_array (size_t len)
            : s (new T [len])
        {}

        ~auto_array() {
            delete[] s;
        }

        T *s;
    };

    std::wstring toString (const Py_UNICODE *u, size_t len) {
        PyObject *s = PyUnicode_FromUnicode (u, len);
        auto_array<wchar_t> w (len);
        PyUnicode_AsWideChar ((PyUnicodeObject *) s, w.s, len);
        Py_DECREF (s);
        return (std::wstring (w.s, len));
    }

    template <>
    inline
    const Py_UNICODE *is_element<Py_UNICODE> (
        const Py_UNICODE *in,
        const Py_UNICODE *end) {
        const Py_UNICODE *result = _is_element (in, end);

        std::wcerr << "is_element ("
                  << toString (in, end - in)
                  << ") --> "
                  << (result
                         ? toString (result, end - result)
                         : std::wstring())
                  << "\n"
            ;

        return (result);
    }

    template<>
    bool is_script_tag<Py_UNICODE> (const Py_UNICODE *s, const Py_UNICODE *e) {
        bool result (_is_script_tag (s, e));

        std::wcerr << "is_script_tag ("
                  << toString (s, e - s)
                  << ") --> "
                  << result
                  << "\n"
            ;

        return (result);
    }
# endif


    /**
     * Handle '<script>' tags
     * They usually begin with '<script' and close with '</script>'.
     */
    template <class Char>
    class drop_manager {
    public:
        drop_manager()
                : drop (false)
            {}

        /*
         * Avoid implicid conversion to int by returning a type which can
         * be converted to bool but not to int.
         */
        typedef bool (drop_manager::*bool_type) (
            const Char *,
            const Char *,
            bool);

        /**
         * The operator bool_type returns true within 'script' tags, otherwise
         * false.
         */
        operator bool_type () const {
            return (drop? &drop_manager<Char>::check: 0);
        }

        /**
         * Look for 'script' tags within two pointers. Set the value of the
         * internal variable 'drop' to the result.
         *
         * @param gi
         * Begin of tag name
         *
         * @param end
         * End of tag name
         *
         * @param newdrop
         * New value for 'drop' if we have a 'script' tag
         *
         * @return
         * New value of internal variable 'drop'.
         */
        bool check (const Char *gi, const Char *end, bool new_drop) {
            if (is_script_tag (gi, end))
                drop = new_drop;

            return (drop);
        }
    private:
        bool drop;
    };

    /**
     * Ignore tags and 'script' tags.
     *
     * @param inp
     * Begin of input string
     *
     * @param end
     * End of input string
     *
     * @param f
     * Function to call for each character which must not be ignored
     *
     * @return
     * false, if no tags can be found
     */
    template <class Char, class CharHandler>
    bool striplm_pass (const Char *inp, const Char *end, CharHandler &f) {
        drop_manager<Char> drop;
        bool in_tag (false);
        bool found (false);
        bool opening_tag (false);
        const Char *gistr = 0;

        while (inp != end) {
            bool keep_char (!in_tag && !drop);
            Char ch (*inp++);

            switch (ch) {
            case '<':
                gistr       = is_element (inp, end);
                in_tag      = gistr != 0;
                keep_char   = !in_tag;
                opening_tag = (inp != end) && (*inp != '/');
                break;

            case '>':
                if (!in_tag)
                    break;

                found  = true;
                in_tag = false;
                // FALL THROUGH
            case ' ':
                if (gistr != 0) {
                    assert (in_tag || (ch == '>'));

                    if (drop.check (gistr, inp - 1, opening_tag))
                        keep_char = false;

                    gistr = 0;
                }
                break;
            }

            if (keep_char)
                f (ch);
        }

        return (found);
    }

    /**
     * Function for counting all characters beyond tags or 'script' tags.
     */
    template <class Char>
    struct counter {
        counter ()
                : len (0)
            {}

        /**
         * Function call.
         * Counts every character.
         */
        void operator() (Char) {
            ++len;
        }

        int length() const {
            return (len);
        }

    private:
        int len;
    };

    /**
     * This function returns all characters beyond tags and 'script' tags.
     */
    template <class Char>
    struct writer {
        /**
         * Constructor.
         *
         * @param out
         * Reference to the first element of char* a[] which is long enaugh to
         * hold the output string.
         */
        writer (Char &out_)
                : out (&out_)
            {}

        /**
         * Function call.
         * Returns the character
         */
        void operator() (const Char &c) {
            *out++ = c;
        }

    private:
        Char *out;
    };

    /**************************************************************
     * Create a pointer to the beginning of the string buffer for
     * the given object.
     */
    template <class Char, class Object>
    Char *make_start (Object *o, const Char * = 0) {
        return (0);
    }

    /// PyStringObject version
    template <>
    char *make_start<char, PyStringObject> (
        PyStringObject *o, const char *) {
        return (o->ob_sval);
    }

    /// PyUnicodeObject version
    template <>
    Py_UNICODE *make_start<Py_UNICODE, PyUnicodeObject> (
        PyUnicodeObject *o,
        const Py_UNICODE *) {
        return (o->str);
    }

    /**************************************************************
     * Creating a string object
     */
    template <class Char, class Object>
    Object *create_string (int len, const Char * = 0, const Object * = 0) {
        return (0);
    }

    /// PyStringObject version
    template <>
    PyStringObject *create_string<char, PyStringObject> (
        int len,
        const char *,
        const PyStringObject *) {
        return ((PyStringObject *) PyString_FromStringAndSize (0, len));
    }

    /// PyUnicodeObject version
    template <>
    PyUnicodeObject *create_string<Py_UNICODE, PyUnicodeObject> (
        int len,
        const Py_UNICODE *,
        const PyUnicodeObject *) {
        return ((PyUnicodeObject *) PyUnicode_FromUnicode (0, len));
    }

    /**
     * Execute stripml for a string.
     *
     * @param input
     * String object to strip
     *
     * @param in
     * Pointer to the object's string buffer
     *
     * @return
     * Stripped string object
     */
    template <class Object, class Char>
    PyObject *do_stripml (Object *input, const Char *in) {
        Object *output = 0;
        const Char *end =
            (in != 0)
                ? (in + PyObject_Length ((PyObject *) input))
                : 0;
        counter<Char> c;
        int len (
            striplm_pass<Char> (in, end, c)
            ? c.length()
            : -1);

        if (len < 0) {
            output = input;
            Py_INCREF (output);
        } else {
            output = create_string<Char, Object> (len, 0, 0);

            if (0 != output) {
                Char *out = make_start<Char, Object> (output, 0);
                writer<Char> w (*out);

                striplm_pass<Char> (in, end, w);
            }
        }

        return ((PyObject *) output);
    }

    PyObject *string_stripml (PyStringObject *input) {
        return (do_stripml (input, input->ob_sval));
    }

    PyObject *unicode_stripml (PyUnicodeObject *input) {
        return (do_stripml (input, input->str));
    }

    extern "C"
    PyObject* stripml (PyObject *self, PyObject *args) {
        PyObject *text = NULL;

        if (!PyArg_UnpackTuple(args, "stripml", 1, 1, &text))
            return (0);

        if (PyUnicode_Check(text))
            return unicode_stripml((PyUnicodeObject*)text);
        else if (PyString_Check(text))
            return string_stripml((PyStringObject*)text);
        else {
            PyErr_SetString(
                PyExc_TypeError,
                "String or unicode string required.");
            return (0);
        }
    }
}

static PyMethodDef module_methods[] = {
    {"stripml", (PyCFunction) stripml, METH_VARARGS,
     "stripml(s) -> string"},
    {NULL, NULL, 0, NULL}
};

#ifndef PyMODINIT_FUNC  /* Declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
extern "C"
PyMODINIT_FUNC
initstripml() {
    PyObject *module;

    module = Py_InitModule3("stripml", module_methods, "");
    if (!module)
        return;
}
