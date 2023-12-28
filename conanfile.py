from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import update_conandata, get, copy, replace_in_file, rmdir
from conan.tools.scm import Git
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class RtMidiConan(ConanFile):
    name = "h264nal"
    version = "0.15"
    url = "https://github.com/TUM-CONAN/conan-h264nal"
    homepage = "https://github.com/chemag/h264nal"
    description = "H264 NAL Parser"
    topics = ("video",)
    license = "BSD"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def requirements(self):
        self.requires("gtest/1.14.0")



    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export(self):
        update_conandata(self, {"sources": {
            "commit": "v{}".format(self.version),
            "url": "https://github.com/chemag/h264nal.git"
            }}
            )

    def source(self):
        git = Git(self)
        sources = self.conan_data["sources"]
        git.clone(url=sources["url"], target=self.source_folder)
        git.checkout(commit=sources["commit"])

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
            """set(CMAKE_CXX_CLANG_TIDY "clang-tidy;-format-style='google'")""",
            """#set(CMAKE_CXX_CLANG_TIDY "clang-tidy;-format-style='google'")""")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
            """add_subdirectory(fuzz)""",
            """#add_subdirectory(fuzz)""")


        replace_in_file(self, os.path.join(self.source_folder, "test", "CMakeLists.txt"),
            """find_library(GTEST_LIBRARY gtest)""",
            """find_package(GTest)""")

        replace_in_file(self, os.path.join(self.source_folder, "test", "CMakeLists.txt"),
            """find_library(GMOCK_LIBRARY gmock)""",
            """#find_library(GMOCK_LIBRARY gmock)""")

        replace_in_file(self, os.path.join(self.source_folder, "test", "CMakeLists.txt"),
            """${GTEST_LIBRARY} gtest_main""",
            """GTest::gtest_main""")
        replace_in_file(self, os.path.join(self.source_folder, "test", "CMakeLists.txt"),
            """${GMOCK_LIBRARY} gmock_main""",
            """GTest::gmock""")

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        # has no cmake install
        #libs
        copy(self, pattern="*.a", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(self.build_folder, "src"))
        copy(self, pattern="*.a", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(self.build_folder, "webrtc"))
        copy(self, pattern="*.so", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(self.build_folder, "src"))
        copy(self, pattern="*.so", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(self.build_folder, "webrtc"))
        copy(self, pattern="*.dylib", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(self.build_folder, "src"))
        copy(self, pattern="*.dylib", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(self.build_folder, "webrtc"))
        copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(self.build_folder, "src"))
        copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(self.build_folder, "webrtc"))
        copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.build_folder, "src"))
        copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.build_folder, "webrtc"))
        #headers
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include", "h264nal"), 
            src=os.path.join(self.build_folder, "src"))
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include", "rtc_base"), 
            src=os.path.join(self.source_folder, "webrtc", "rtc_base"))
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include", "h264nal"), 
            src=os.path.join(self.source_folder, "include"))



    def package_info(self):
        self.cpp_info.components["h264nal"].includedirs = [os.path.join("include")]
        self.cpp_info.components["h264nal"].libs = ["h264nal"]
        self.cpp_info.components["h264nal_webrtc"].includedirs = [os.path.join("include", "rtc_base")]
        self.cpp_info.components["h264nal_webrtc"].libs = ["webrtc"]
